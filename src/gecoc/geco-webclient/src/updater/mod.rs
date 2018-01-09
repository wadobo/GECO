mod msg;
mod login;
mod list;
mod context;

use yew::format::Json;

pub use self::msg::Msg;
pub use self::context::Context;
pub use self::context::KEY;
use model::Model;

pub fn update(context: &mut Context, model: &mut Model, msg: Msg) {
    match msg {
        // login
        Msg::Login => login::login(context, model),
        Msg::Logout => login::logout(context, model),
        Msg::LoginReady(st) => login::login_ready(context, model, st),
        Msg::LoginSetUserName(uname) => model.login.username = uname,
        Msg::LoginSetPassword(pwd) => model.login.password = pwd,
        // register
        Msg::Register => login::register(context, model),
        Msg::RegisterUserName(uname) => model.register.username = uname,
        Msg::RegisterPassword(pwd) => model.register.password = pwd,
        Msg::RegisterRepeat(pwd) => model.register.repeat = pwd,
        Msg::RegisterReady(st) => login::register_ready(context, model, st),
        // list
        Msg::AllPassReady(st) => list::all_pass_ready(context,model, st),
    };
    context.storage.store(KEY, Json(&model));
}
