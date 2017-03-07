from metronus_app.model.actor import Actor


class Employee(Actor):

    def __unicode__(self):
        return self.identifier
