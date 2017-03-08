from metronus_app.model.role import Role

def populate_roles():
    print("==== POPULATING ROLES ====")
    Role.objects.create(name="Administrator")
    Role.objects.create(name="Project manager")
    Role.objects.create(name="Department manager")
    Role.objects.create(name="Coordinator")
    Role.objects.create(name="Team manager")
    Role.objects.create(name="Employee")
    print("==== %d ROLES INSERTED ====" % Role.objects.all().count())


def populate_database():
    populate_roles()