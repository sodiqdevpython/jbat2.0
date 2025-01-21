from rest_framework import serializers
from organizations.models import RoomsEquipment, Organizations

class RoomsEquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomsEquipment
        fields = [
            'id', 'name', 'measure_type', 'amount', 'avilable_type',
            'accepted_date', 'invert_number', 'entered_date', 'when_first_time_used',
            'when_made', 'image1', 'image2', 'image3', 'penny_by_year',
            'xarakteri', 'equipment_type', 'author', 'organization_for',
            'command_file', 'created', 'updated', 'is_active'
        ]


class OrganizationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizations
        fields = [
            "id", "organization_number", "name", "education_type", 
            "power", "is_inclusive", "students_amount", "region", 
            "district", "city", "latitude", "longitude", "ball",
            "created", "updated"
        ]