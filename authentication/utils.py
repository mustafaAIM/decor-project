def error_message(en,ar):
  return {
            "error":{
              "en":en,
              "ar":ar,
            }
          }

def generate_random_otp() -> str:
  import random
  otp = random.randint(100000, 999999)
  return otp