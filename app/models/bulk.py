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
                               uselist=True)
    csv_header_row = db.relationship('CsvHeaderRow',
                                     backref='csv_header_row_container',
                                     uselist=False)

    def cell_data(self, row_num, cell_num):
        if row_num < 0 or row_num >= len(self.csv_rows):
            raise ValueError('Invalid row number')
        if cell_num < 0 or cell_num >= len(self.csv_rows[row_num].csv_cells):
            raise ValueError('Invalid cell number')
        return '%s' % self.csv_rows[row_num].csv_cells[cell_num].data

    def __repr__(self):
        return '<CsvContainer \'%s\'>' % self.file_name


class CsvHeaderRow(db.Model):
    """
    Schema for a header row in a CSV file. Cells should be added in the order
    that they appeared in the original row of the CSV file.
    """
    __tablename__ = 'csv_header_rows'
    id = db.Column(db.Integer, primary_key=True)
    csv_container_id = db.Column(db.Integer,
                                 db.ForeignKey('csv_containers.id'))
    csv_cells = db.relationship('CsvHeaderCell', backref='csv_header_row',
                                uselist=True)


class CsvBodyRow(db.Model):
    """
    Schema for a content row in a CSV file. Cells should be added in the order
    that they appeared in the original row of the CSV file.
    """
    __tablename__ = 'csv_body_rows'
    id = db.Column(db.Integer, primary_key=True)
    csv_container_id = db.Column(db.Integer,
                                 db.ForeignKey('csv_containers.id'))
    csv_cells = db.relationship('CsvBodyCell', backref='csv_body_row',
                                uselist=True)


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


class CsvBodyCell(db.Model):
    """
    Schema for a cell in a CSV file. Each cell contains one comma-separated
    string in a row of a CSV file.
    """
    __tablename__ = 'csv_cells'
    id = db.Column(db.Integer, primary_key=True)
    csv_row_id = db.Column(db.Integer, db.ForeignKey('csv_body_rows.id'))
    data = db.Column(db.Text)

    # TODO: Should be `CsvHeaderCell` instead of `CsvHeaderRow` (<- should
    # TODO: still exist but the same class)
