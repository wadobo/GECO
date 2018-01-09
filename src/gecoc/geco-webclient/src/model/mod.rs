mod login;

pub use self::login::LoginModel;
pub use self::login::RegisterModel;

#[derive(Serialize, Deserialize)]
pub struct Model {
    pub login: LoginModel,
    pub register: RegisterModel,
}

impl Model {
    pub fn new() -> Model {
        Model {
            login: LoginModel::new(),
            register: RegisterModel::new(),
        }
    }
}
