from metronus_app.model.actor import Actor


class Administrator(Actor):
	"""
	Admin can handle projects, departments, tasks, employees, roles, etc. from his/her company
	"""
    def __unicode__(self):
        return self.identifier
