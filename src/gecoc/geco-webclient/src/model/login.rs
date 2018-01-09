#[derive(Serialize, Deserialize)]
pub struct LoginModel {
    pub token: Option<String>,
    pub username: Option<String>,
    pub password: Option<String>,
    pub error: Option<String>,
}

impl LoginModel {
    pub fn new() -> LoginModel {
        LoginModel {
            token: None,
            username: None,
            password: None,
            error: None,
        }
    }
}

#[derive(Serialize, Deserialize)]
pub struct RegisterModel {
    pub username: Option<String>,
    pub password: Option<String>,
    pub repeat: Option<String>,
    pub error: Option<String>,
}

impl RegisterModel {
    pub fn new() -> RegisterModel {
        RegisterModel {
            username: None,
            password: None,
            repeat: None,
            error: None,
        }
    }
}
