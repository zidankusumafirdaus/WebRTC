from werkzeug.security import check_password_hash
from apps.utils.supabase_client import get_supabase_client


def verify_credentials(username: str, password: str):
    supabase = get_supabase_client()
    # Try users
    resp = supabase.table("users").select("*").eq("username", username).execute()
    user_data = resp.data
    table = "users"
    if not user_data:
        # Try counselors
        resp = (
            supabase.table("counselors").select("*").eq("username", username).execute()
        )
        user_data = resp.data
        table = "counselors"
    if not user_data:
        return None
    user = user_data[0]
    if not check_password_hash(user["password"], password):
        return None
    return {
        "id": user["user_id"] if table == "users" else user["counselor_id"],
        "role": user["role"],
        "display_name": user.get("display_name"),
    }


def is_username_available(username: str) -> bool:
    supabase = get_supabase_client()
    resp_u = (
        supabase.table("users").select("user_id").eq("username", username).execute()
    )
    resp_c = (
        supabase.table("counselors")
        .select("counselor_id")
        .eq("username", username)
        .execute()
    )
    return not (resp_u.data or resp_c.data)


def create_user(username: str, hashed_password: str, display_name: str) -> int:
    supabase = get_supabase_client()
    new_user = {
        "username": username,
        "password": hashed_password,
        "display_name": display_name,
        "role": "user",
    }
    resp = supabase.table("users").insert(new_user).execute()
    return int(resp.data[0]["user_id"])


def create_counselor(
    username: str,
    hashed_password: str,
    display_name: str,
    bio=None,
    qualifications=None,
) -> int:
    supabase = get_supabase_client()
    new_counselor = {
        "username": username,
        "password": hashed_password,
        "display_name": display_name,
        "bio": bio,
        "qualifications": qualifications,
        "role": "counselor",
    }
    resp = supabase.table("counselors").insert(new_counselor).execute()
    return int(resp.data[0]["counselor_id"])
