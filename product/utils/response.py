def custom_message(en,ar,status):
    return {
        "message":{
            "status":str(status),
            "en":str(en),
            "ar":str(ar),
        }
    }