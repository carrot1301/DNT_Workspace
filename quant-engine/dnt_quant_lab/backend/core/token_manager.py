from fastapi import HTTPException
from core.supabase_client import get_supabase

def check_and_deduct_tokens(user_id: str, cost: int = 1) -> bool:
    """
    Checks if the user has enough tokens (free or paid) and deducts them.
    Free credits are prioritized.
    Returns True if successful, raises HTTPException 402 if insufficient.
    """
    supabase = get_supabase()
    
    try:
        # 1. Get user profile using the service role client
        response = supabase.table('profiles').select('free_credits, paid_tokens').eq('id', user_id).single().execute()
        profile = response.data
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
            
        free = profile.get('free_credits', 0)
        paid = profile.get('paid_tokens', 0)
        
        if free + paid < cost:
            raise HTTPException(status_code=402, detail="Hết lượt sử dụng. Vui lòng nạp thêm Token để tiếp tục!")
            
        # 2. Deduct logic
        if free >= cost:
            new_free = free - cost
            new_paid = paid
        else:
            remaining_cost = cost - free
            new_free = 0
            new_paid = paid - remaining_cost
            
        # 3. Update profile
        supabase.table('profiles').update({
            'free_credits': new_free,
            'paid_tokens': new_paid
        }).eq('id', user_id).execute()
        
        return True
    except HTTPException:
        raise
    except Exception as e:
        print(f"Token deduction error: {e}")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi xử lý Token")
