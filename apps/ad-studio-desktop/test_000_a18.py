from ad_studio import models
R = models.Project
class P(R):
    def __init__(self, id, name=None, task_type=None, **kw):
        super().__init__(id=id, product_name=name or "", platform="", form="", level=1, actor_id=None, scene_id=None, shots=[], **kw)
        if task_type:
            self.creative_plan["task_type"] = task_type
models.Project = P
