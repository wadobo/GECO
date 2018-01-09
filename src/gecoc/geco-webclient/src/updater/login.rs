use serde_json::Value as JsonValue;

use updater::Msg;
use updater::Context;
use updater::list;
use model::Model;

fn do_login(context: &mut Context, model: &mut Model) {
    let data = json!({
        "user": model.login.username.clone().unwrap_or_default(),
        "password": model.login.password.clone().unwrap_or_default(),
    });

    context.post("auth", data, |data| Msg::LoginReady(data));
}

pub fn login(context: &mut Context, model: &mut Model) {
    model.login.error = None;
    do_login(context, model);
    model.login.password = None;
}

pub fn login_ready(context: &mut Context, model: &mut Model, st: Result<JsonValue, ()>) {
    model.login.token = match st {
        Ok(json) => match json["data"].as_str() {
            Some(tk) => Some(String::from(tk)),
            None => {
                model.login.error = Some(String::from("Login Error, try again"));
                None
            }
        },
        Err(_) => {
            model.login.error = Some(format!("API Error"));
            None
        }
    };
    list::get_all_pass(context, model);
}

pub fn logout(_: &mut Context, model: &mut Model) {
    model.login.username = None;
    model.login.password = None;
    model.login.token = None;
    model.login.error = None;
}

pub fn register(context: &mut Context, model: &mut Model) {
    let m = &mut model.register;
    m.error = None;

    let uname = m.username.clone().unwrap_or_default();
    let pwd = m.password.clone().unwrap_or_default();
    let repeat = m.repeat.clone().unwrap_or_default();

    if pwd != repeat {
        m.error = Some(format!("Passwords didn't match"));
        return;
    }

    if pwd.is_empty() || repeat.is_empty() || uname.is_empty() {
        m.error = Some(format!("All fields are required"));
        return;
    }

    let data = json!({
        "user": uname,
        "password": pwd,
    });

    context.post("register", data, |d| Msg::RegisterReady(d));
}

pub fn register_ready(context: &mut Context, model: &mut Model, st: Result<JsonValue, ()>) {
    match st {
        Ok(json) => match json["status"].as_str() {
            Some(s) if s == "ok" => {
                model.login.username = model.register.username.clone();
                model.login.password = model.register.password.clone();
                do_login(context, model);

                model.login.username = None;
                model.login.password = None;
                model.register.username = None;
                model.register.password = None;
                model.register.repeat = None;
            }
            _ => {
                model.register.error = Some(String::from("Registration Error"));
            }
        },
        Err(_) => {
            model.register.error = Some(format!("API Error"));
        }
    };
}
