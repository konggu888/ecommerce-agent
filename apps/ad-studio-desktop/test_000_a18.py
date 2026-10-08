from ad_studio import models
Base = models.Project
class Compat(Base):
    def __init__(self, *args, **kw):
        name = kw.pop("name", None)
        task_type = kw.pop("task_type", None)
        if name is not None and "product_name" not in kw and not args:
            kw["product_name"] = name
        super().__init__(*args, **kw)
        if task_type:
            self.creative_plan["task_type"] = task_type
setattr(models, "Project", Compat)
