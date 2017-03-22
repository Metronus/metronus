from metronus_app.model.actor import Actor


class Administrator(Actor):

    def __unicode__(self):
        return self.identifier
