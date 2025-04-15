from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_client_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['user_id'] = user.id
    refresh['email'] = user.email
    refresh['type'] = 'client'
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
