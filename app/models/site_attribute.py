from .. import db
import os


class SiteAttribute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attr_name = db.Column(db.String(100), unique=True)
    value = db.Column(db.Text)

    @staticmethod
    def get(attr):
        attribute = SiteAttribute.query.filter_by(attr_name=attr).first()
        if attribute is None:
            attribute = SiteAttribute(attr_name=attr)
            if attr in os.environ:
                attribute.value = os.environ[attr]
            elif attr == "ORG_NAME":
                attribute.value = "Maps4All"
            else:
                attribute.value = ""

            db.session.add(attribute)
            db.session.commit()

        return attribute

    @staticmethod
    def get_value(attr):
        return SiteAttribute.get(attr).value
