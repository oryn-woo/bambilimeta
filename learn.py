import datetime


class Employee:
    raise_amount = 1.04  # a class variable
    num_of_emps = 0  # It should be same across all instances.

    def __init__(self, first, last, pay) -> None:
        self.first = first
        self.last = last
        self.pay = pay
        Employee.num_of_emps += 1  # This is overriden for all instances, if self, it will be for the particular instance
    @property
    def fullname(self):
        """
        Decorated so it remains as an attribute same for email.
        Now to be able to alter the full name and automatically
         apply the changes to the class, e.g., so the email
         constructed properly. We use a setter.
        :return:
        """
        return "{} {}".format(self.first, self.last)

    @fullname.setter
    def fullname(self, name):
        """
        Setter will require its own value by default which we
         collect as name
        :param name: Setters parameter
        :return: Split fullname
        """
        first, last = name.split(" ")
        self.first = first
        self.last = last

    @fullname.deleter
    def fullname(self):
        """
        Gets runed when a name is deleted
        :return: None
        """
        print("Delete Name")
        self.first = None
        self.last = None



    def apply_raise(self):
        """
        we can access raise amount directly, or through the instance.
        Doing it through the instance (self), allows us to modify and
        use unique ones for each instance. But doing it
        directly without safe, will make it unavailable
        in the instances namespace, so we can modify it.
        """
        self.pay = int(self.pay * self.raise_amount)

    @classmethod
    def set_raise_amount(cls, amount):
        """"
        This method works with the class so it modifies the raise amount on
        all instances of the class.
        So eventually wither we access it from the instance emp_1.raise_amount(), or from
        the class itself Employee.set_raise_amount(amount), it works on all instances.
        """
        cls.raise_amount = amount

    @classmethod
    def from_string_constructor(cls, emp_str):
        first, last, pay = emp_str.split('-')
        return cls(first, last, pay)

    @staticmethod
    def is_work_day(day):
        """
        This is made static because we are neither using any instance
        variable of cls variable
        """
        if day.weekday == 5 or day.weekday == 6:
            return False
        return True
    @property
    def email(self):
        return "{}.{}@gmail.com".format(self.first, self.last)


    def __repr__(self):
        """
        A more unambigous representation of the object, meant for developers
        Its used as a fallback if __str__ is not given.
        :return: Construction of the object
        """
        return "Employee({}, {}, {})".format(self.first, self.last, self.pay)

    def __str__(self):
        return "{} - {}".format(self.full_name(), self.email)

    def __add__(self, other):
        """Add two employees together by adding their salaries.
        It acts like our own addition, but when called on our
         own instance, adds salary
        """
        return self.pay + other.pay

    def __len__(self):
        """
        Get length. Help get employee name length, e.g when filling
         documents.
        :return:
        """
        return len(self.full_name())



emp_1 = Employee("John", "Smith", 5000)
emp_1.fullname = "Corey Schafer"
print(emp_1.email)
print(emp_1.fullname)

del emp_1.fullname

print(emp_1.email)
print(emp_1.fullname)


class Developer(Employee):
    """
    All the attributes and methods are inherited.
    If we try creating and instance and accessing attributes it
    does not have, python walks up the chain of inheritance until
    it finds it.x
    (call resolution)
    """
    raise_amount = 1.10  # This is changed only for the developer class.

    # To add more attributes, we use it's own init method
    def __init__(self, first, last, pay, prog_lang) -> None:
        super().__init__(first, last, pay)  # Let Employees inti method handle this method
        self.prog_lang = prog_lang


class Manager(Employee):
    def __init__(self, first, last, pay, employees=None) -> None:
        super().__init__(first, last, pay)
        if employees is None:
            self.employees = []  # Never pass mutable data types as default values.
        else:
            self.employees = employees

    def add_employee(self, emp):
        if emp not in self.employees:
            self.employees.append(emp)

    def remove_employee(self, emp):
        if emp in self.employees:
            self.employees.remove(emp)

    def print_emps(self):
        for emp in self.employees:
            print("---->", emp.full_name())

#
# dev_1 = Developer("dev", "memi", 6000, "python")
# dev_2 = Developer("dev", "fevi", 56000, "java")
# mgr_1 = Manager("sue", "smith", 90000, [dev_1])
# emp_1 = Employee("john", "due", 500)
# emp_2 = Employee("Peter", "dear", 500)
# print(emp_1.__repr__())
# print(emp_1.__str__())
# print(int.__add__(2, 2))
# print("test".__len__())
# print(emp_1 + emp_2)
# print(len(emp_1))
