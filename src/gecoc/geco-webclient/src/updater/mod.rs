mod msg;
mod login;
mod context;

pub use self::msg::Msg;
pub use self::context::Context;
use model::Model;

pub fn update(context: &mut Context, model: &mut Model, msg: Msg) {
    match msg {
        // login
        Msg::Login => login::login(context, &mut model.login),
        Msg::Logout => login::logout(context, &mut model.login),
        Msg::LoginReady(st) => login::login_ready(context, &mut model.login, st),
        Msg::LoginSetUserName(uname) => model.login.username = uname,
        Msg::LoginSetPassword(pwd) => model.login.password = pwd,
    }
}
