from app.schemas.leave import Leave

class LeaveDB:
    # Here we store the leave records where the key is leave_id and value is Leave Object
    __leaves = {}

    @classmethod
    def add_Leave(cls, leave_id:str, leave:Leave):
        cls.__leaves[leave_id] = leave
        return {'message': "Leave applied successfully"}
    
    @classmethod
    def get_Leave(cls, leave_id:str):
        return cls.__leaves.get(leave_id)
    
    @classmethod
    def get_all_leaves(cls):
        return cls.__leaves
    
    @classmethod
    def update_Leave(cls, leave_id:str, leave:Leave):
        cls.__leaves[leave_id] = leave
        return {'message': "Leave updated successfully"}
    
    @classmethod
    def delete_leave(cls, leave_id:str):
        del cls.__leaves[leave_id]
        return {'message': "Leave deleted successfully"} 