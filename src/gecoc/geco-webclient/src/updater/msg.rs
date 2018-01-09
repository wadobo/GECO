use serde_json::Value as JsonValue;

pub static BASE: &str = "/api";

pub enum Msg {
    Login,
    Logout,
    LoginSetUserName(Option<String>),
    LoginSetPassword(Option<String>),
    LoginReady(Result<JsonValue, ()>),

    Register,
    RegisterUserName(Option<String>),
    RegisterPassword(Option<String>),
    RegisterRepeat(Option<String>),
    RegisterReady(Result<JsonValue, ()>),

    AllPassReady(Result<JsonValue, ()>),
}
