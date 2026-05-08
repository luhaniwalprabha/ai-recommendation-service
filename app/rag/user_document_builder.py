class UserDocumentBuilder:
    def build(self, interaction) -> str:
        parts = [
            f"User ID: {interaction['user_id']}",
            f"Action: {interaction['action']}",
            f"Product: {interaction['product_name']}",
            f"Category: {interaction.get('category')}",
            f"Timestamp: {interaction.get('timestamp')}",
        ]

        return "\n".join([p for p in parts if p])