from django.db import models

# Create your models here.

class Chest(models.Model):
    # X光相片主键id
    chest_x_ray_id = models.AutoField(primary_key=True)
    # 患者id
    patient_id = models.IntegerField()
    # 患者 X 光序号
    x_ray_id = models.IntegerField()
    # 病症列表
    disease = models.BigIntegerField()

    def __str__(self):
        return  '患者：  ' + str(self.patient_id) + '-' + str(self.x_ray_id)