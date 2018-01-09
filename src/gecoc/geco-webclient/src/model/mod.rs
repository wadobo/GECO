mod login;
mod list;

pub use self::login::LoginModel;
pub use self::login::RegisterModel;
pub use self::list::ListModel;
pub use self::list::PassModel;

#[derive(Serialize, Deserialize)]
pub struct Model {
    pub login: LoginModel,
    pub register: RegisterModel,
    pub list: ListModel,
    pub error: Option<String>,
    pub info: Option<String>,
}

impl Model {
    pub fn new() -> Model {
        Model {
            login: LoginModel::new(),
            register: RegisterModel::new(),
            list: ListModel::new(),
            error: None,
            info: None,
        }
    }
}
