from FamilyApp.models import FamilyMember, Relationship
class Helper:
    @staticmethod
    def get_ancestors(member, ancestors=None):
        if ancestors is None:
            ancestors = []

        # Find parents (or other ancestor relationships as needed)
        parent_relationships = Relationship.objects.filter(
            related_person=member, relationship_type='Parent'
        )

        for relationship in parent_relationships:
            parent = relationship.person
            ancestors.append({
                'full_name': parent.full_name,
                'user_profile_img': parent.user_profile_img,
                'relationship': relationship.relationship_type,
                'children': Helper.get_ancestors(parent)  # Recursive call
            })

        return ancestors
    
    @staticmethod
    def get_descendants(member, descendants=None):
        if descendants is None:
            descendants = []

    # Find children (or other descendant relationships as needed)
        child_relationships = Relationship.objects.filter(
            person=member, relationship_type='Parent'
        )

        for relationship in child_relationships:
            child = relationship.related_person
            descendants.append({
                'full_name': child.full_name,
                'user_profile_img': child.user_profile_img,
                'relationship': relationship.relationship_type,
                'children': Helper.get_descendants(child)  # Recursive call
            })

        return descendants


