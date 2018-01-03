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
