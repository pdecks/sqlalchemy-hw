
"""Sample file demonstrating SQLAlchemy joins & relationships."""

from flask_sqlalchemy import SQLAlchemy


# This is the connection to the SQLite database; we're getting this
# through the Flask-SQLAlchemy helper library. On this, we can find
# the `session` object, where we do most of our interactions
# (like committing, etc.)

db = SQLAlchemy()


####################################################################
# Model definitions


class Employee(db.Model):
    """Employee."""

    __tablename__ = "employees"

    emp_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    state = db.Column(db.String(2), nullable=False, default='CA')
    fav_color = db.Column(
        db.String(20), nullable=True, default='Unknown')
    dept_code = db.Column(
        db.Integer, db.ForeignKey('departments.dept_code'))

    dept = db.relationship(
        'Department',
        backref=db.backref('employees', order_by=emp_id))

    def __repr__(self):
        return "<Employee id=%s name=%s>" % (self.emp_id, self.name)


class Department(db.Model):
    """Department. A department has many employees."""

    __tablename__ = "departments"

    dept_code = db.Column(db.String(5), primary_key=True)
    dept = db.Column(db.String(20), nullable=True, unique=True)
    phone = db.Column(db.String(20))

    def __repr__(self):
        return "<Dept id=%s name=%s>" % (self.dept_code, self.dept)


def example_data():
    """Create some sample data."""

    # In case this example_data function is run more than once,
    # let's delete all the existing departments and employees,
    # so we don't have an error when we try to add them.
    Department.query.delete()
    Employee.query.delete()

    ded = Department(
        dept_code='ed', dept='Education', phone='555-1000')
    dad = Department(
        dept_code='admin', dept='Administration', phone='555-2222')
    dpt = Department(
        dept_code='pt', dept='Part-Time', phone='555-9999')
    dot = Department(
        dept_code='oth', dept='Other', phone='555-3333')

    employees = [
        Employee(name='Joel Burton', dept=ded, fav_color='orange'),
        Employee(name='Cynthia Dueltgen', dept=ded, fav_color='purple'),
        Employee(name='Rachel Thomas', dept=ded),
        Employee(name='Katie Lefevre', dept=ded, fav_color='rainbow'),
        Employee(name='Meggie Mahnken', dept=ded, fav_color='black'),
        Employee(name='Heather Bryant', dept=ded, fav_color='purple'),
        Employee(name='Kristen McClure', dept=ded, fav_color='orange'),
        Employee(name='Lavinia Karl', dept=ded),
        Employee(name='Denise Wiedl', dept=ded),
        Employee(name='David Phillips', dept=dad),
        Employee(name='Angie Chang', dept=dad),
        Employee(name='Stefan Gomez', dept=dad),
        Employee(name='Laura Gillen', dept=dad),
        Employee(name='Paria Rajai', dept=dad),
        Employee(name='Wendy Saccuzzo', dept=dot),
        Employee(name='Dori Grant', dept=dot),
        Employee(name='Kari Burge', dept=dot, fav_color='purple'),
        Employee(name='Rachel Walker', dept=dpt),
        Employee(name='Anna Akullian', dept=dpt),
        Employee(name='Jumal Qazi', dept=dpt, fav_color='orange'),
        Employee(name='Balloonicorn', fav_color='rainbow'),
    ]
    db.session.add_all(employees)
    db.session.commit()


def all_employees_nav():
    """Find phone roster for employees & their departments.

    For every employee in a department, return the employee name,
    their department name, and the department phone number.

    Returns list of objects.
    """

    emps = db.session.query(Employee)
    emps_with_dept = emps.filter(Employee.dept_code.isnot(None))

    # We'll do this by handing back the employee objects.
    # In our template, we can get the department info by using
    # the 'dept' attribute -- but that will fire off a query
    # for every single dept (use the FlaskDebugToolbar to
    # verify this)
    return emps_with_dept.all()

    # *Advanced Note*: there is a way to do this efficiently,
    # using an advanced idea we haven't talked about -- telling
    # the ORM to load all of this stuff up-front, at once.
    #
    # If we change that "emps =" line to:
    #   emps = (db.session.query(Employee).
    #                      options(db.joinedload('dept')))
    # then it will pre-load all the departments at once.
    #
    # You can read about this advanced technique at:
    # http://docs.sqlalchemy.org/en/latest/orm/loading_relationships.html
    #
    # Or, as a more general solution, we can use the technique
    # show in all_employees_join, below.


def all_employees_join():
    """Find phone roster for employees & their departments.

    For every employee in a department, return the employee name,
    their department name, and the department phone number.
    
    Returns list of tuples.
    """

    # This time, we'll do this by directly querying just the
    # stuff we need -- name, dept, phone -- and by doing the
    # join ourelves. This will be one query, rather than many,
    # as in the function above.
    emps = db.session.query(Employee.name,
                            Department.dept,
                            Department.phone).join(Department)

    return emps.all()


def raw_sql_query():
    """Show how to query in raw SQL, bypassing SQLAlchemy ORM.

    Sometimes, there may be questions that are just easier
    to ask using the SQL you know, rather than learning how to
    do it with an ORM.
    
    We can bypass and use raw SQL directly if that's easier.

    For example, let's ask the question: "show us the counts
    of the number of employees who like orange in each department"
    """

    SQL = """
        SELECT dept_code,
               dept,
               COUNT(*) AS num_emps
        FROM Departments
            JOIN Employees USING (dept_code)
        WHERE fav_color='orange'
        GROUP BY dept_code
        ORDER BY dept
    """

    results = db.engine.execute(SQL).fetchall()
    return results

    # It would be possible to write this query going through the
    # ORM -- you'd just need to learn a bit more about the ORM
    # to do so. If you're interested, here's how we could
    # write that same query via the ORM:

    # results = (db.session.query(Department.dept_code,
    #                             Department.dept,
    #                             db.func.count())
    #                      .join(Employee)
    #                      .filter(Employee.fav_color == 'orange')
    #                      .group_by(Department)
    #                      .order_by(Department.dept)
    #           ).all()
    # return results




####################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emp.db'
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)

    # Create our tables and some sample data
    db.create_all()
    example_data()


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will
    # leave you in a state of being able to work with the database
    # directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."

    # grab the employee object with the name 'Cynthia Dueltgen'
    cynthia = Employee.query.filter(Employee.name == 'Cynthia Dueltgen').one()

    # what department is she in? (she the object for her department)
    print cynthia.dept

    # what is the phone number of the department that Cynthia is in?
    print cynthia.dept.phone

    # Find all employees where we don't know which department they belong to (Null dept_code)
    emp_without_dept = Employee.query.filter(Department.dept_code.is_(None)).all()
    print emp_without_dept

    # Get a list of tuples with just the name of everyone whose favorite color is orange
    emp_orange = db.session.query(Employee.name).filter(Employee.fav_color == 'orange').all()

    # Find all employees who work in 'Administration'
    # objects
    emp_admin = db.session.query(Employee).filter(Department.dept == 'Administration').all()
    # names only
    emp_admin_names = db.session.query(Employee.name).filter(Department.dept == 'Administration').all()