mod login;

pub use self::login::LoginModel;

pub struct Model {
    pub login: LoginModel,
}

impl Model {
    pub fn new() -> Model {
        Model {
            login: LoginModel::new(),
        }
    }
}
