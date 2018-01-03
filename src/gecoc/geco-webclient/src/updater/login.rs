use yew::services::fetch::Method;
use yew::format::Json;
use serde_json::Value as JsonValue;

use updater::Msg;
use updater::Context;
use updater::msg::BASE;
use model::LoginModel;

pub fn login(context: &mut Context, model: &mut LoginModel) {
    model.error = None;

    context.console.log(&format!("Login {:?} {:?}", model.username, model.password));
    let uname = model.username.clone().unwrap_or_default();
    let pwd = model.password.clone().unwrap_or_default();
    let data = json!({
        "user": uname,
        "password": pwd,
    });

    model.password = None;

    context.web.fetch(Method::Post,
                  &format!("{}/auth", BASE),
                  Json(&data),
                  |Json(data)| Msg::LoginReady(data));
}

pub fn login_ready(_: &mut Context, model: &mut LoginModel, st: Result<JsonValue, ()>) {
    model.token = match st {
        Ok(json) => match json["data"].as_str() {
            Some(tk) => Some(String::from(tk)),
            None => {
                model.error = Some(String::from("Login Error, try again"));
                None
            }
        },
        Err(_) => {
            model.error = Some(format!("API Error"));
            None
        }
    };
}

pub fn logout(_: &mut Context, model: &mut LoginModel) {
    model.username = None;
    model.password = None;
    model.token = None;
    model.error = None;
}
