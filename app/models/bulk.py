import csv
import StringIO

from sqlalchemy import desc

from .. import db


class CsvContainer(db.Model):
    """
    Schema for contents of CSV files that are uploaded for bulk resource
    management. Rows should be added in the order that they appeared in the
    original CSV file.
    """
    __tablename__ = 'csv_containers'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(64))
    date_uploaded = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    csv_rows = db.relationship('CsvBodyRow', backref='csv_container',
                               uselist=True, cascade='delete')
    csv_header_row = db.relationship('CsvHeaderRow',
                                     backref='csv_header_row_container',
                                     uselist=False, cascade='delete')

    def cell_data(self, row_num, cell_num):
        if row_num < 0 or row_num >= len(self.csv_rows):
            raise ValueError('Invalid row number')
        if cell_num < 0 or \
                cell_num >= len(self.csv_rows[row_num].csv_body_cells):
            raise ValueError('Invalid cell number')
        return '%s' % self.csv_rows[row_num].csv_body_cells[cell_num].data

    def predict_options(self):
        for i, column in enumerate(self.csv_header_row.csv_header_cells):
            if column.descriptor_type == 'option':
                predicted_options = set()
                for j in range(len(self.csv_rows)):
                    predicted_options.add(self.cell_data(j, i))
                column.predicted_options = predicted_options
                db.session.add(column)
        db.session.commit()

    def __repr__(self):
        return '<CsvContainer \'%s\'>' % self.file_name

    @staticmethod
    def most_recent(user):
        return CsvContainer.query.filter_by(user=user).order_by(
            desc(CsvContainer.date_uploaded)
        ).limit(1).first()


class CsvHeaderRow(db.Model):
    """
    Schema for a header row in a CSV file. Cells should be added in the order
    that they appeared in the original row of the CSV file.
    """
    __tablename__ = 'csv_header_rows'
    id = db.Column(db.Integer, primary_key=True)
    csv_container_id = db.Column(db.Integer,
                                 db.ForeignKey('csv_containers.id'))
    csv_header_cells = db.relationship('CsvHeaderCell',
                                       backref='csv_header_row',
                                       uselist=True, cascade='delete')


class CsvBodyRow(db.Model):
    """
    Schema for a content row in a CSV file. Cells should be added in the order
    that they appeared in the original row of the CSV file.
    """
    __tablename__ = 'csv_body_rows'
    id = db.Column(db.Integer, primary_key=True)
    csv_container_id = db.Column(db.Integer,
                                 db.ForeignKey('csv_containers.id'))
    csv_body_cells = db.relationship('CsvBodyCell', backref='csv_body_row',
                                     uselist=True, cascade='delete')


class CsvHeaderCell(db.Model):
    """
    Schema for a header cell in a CSV file. Each cell contains one
    comma-separated string in the first row of a CSV file.
    """
    __tablename__ = 'csv_header_cells'
    id = db.Column(db.Integer, primary_key=True)
    csv_header_row_id = db.Column(db.Integer,
                                  db.ForeignKey('csv_header_rows.id'))
    data = db.Column(db.Text)
    descriptor_type = db.Column(db.Integer)  # 'option' or 'text'
    predicted_options = db.Column(db.PickleType)  # Set of options (strings)
    new_options = db.Column(db.PickleType)  # Set of options (strings)

    def predicted_options_string(self):
        l = list(self.predicted_options)
        l.sort()
        return ', '.join(map(str, l))

    def new_options_string(self):
        l = list(self.new_options)
        l.sort()
        return ', '.join(map(str, l))

    def add_new_options_from_list(self, new_options_list):
        new_options = set()
        for new_option in new_options_list:
            new_options.add(new_option.strip())
        self.new_options = new_options
        db.session.add(self)
        db.session.commit()

    def add_new_options_from_string(self, new_options_string):
        l = []
        csv_reader = csv.reader(StringIO.StringIO(new_options_string))
        for row in csv_reader:
            for option in row:
                option = option.strip()
                if len(option) > 0:
                    l.append(option)
        self.add_new_options_from_list(l)


class CsvBodyCell(db.Model):
    """
    Schema for a cell in a CSV file. Each cell contains one comma-separated
    string in a row of a CSV file.
    """
    __tablename__ = 'csv_cells'
    id = db.Column(db.Integer, primary_key=True)
    csv_row_id = db.Column(db.Integer, db.ForeignKey('csv_body_rows.id'))
    data = db.Column(db.Text)
