use serde_json::Value as JsonValue;

use updater::Msg;
use updater::Context;
use model::Model;
use model::PassModel;

macro_rules! jstr {
    ($js: expr) => {{
        $js.as_str().unwrap_or_default().to_string()
    }}
}

pub fn get_all_pass(context: &mut Context, model: &mut Model) {
    if let Some(ref tk) = model.login.token {
        let data = json!({ "cookie": tk });
        context.post("get_all_passwords", data, |data| Msg::AllPassReady(data));
    }
}

pub fn all_pass_ready(_context: &mut Context,
                      model: &mut Model,
                      st: Result<JsonValue, ()>) {
    match st {
        Ok(json) => {
            let passwds = &mut model.list.passwords;
            if let Some(pwds) = json["data"].as_array() {
                for pwd in pwds {
                    passwds.push(PassModel{
                        name: jstr!(pwd["name"]),
                        ptype: jstr!(pwd["type"]),
                        desc: jstr!(pwd["description"]),
                        account: jstr!(pwd["account"]),
                        password: jstr!(pwd["password"]),
                        cypher: jstr!(pwd["cypher_method"]),
                        updated: pwd["updated"].as_f64().unwrap_or_default(),
                        expiration: pwd["expiration"].as_f64().unwrap_or_default(),
                    });
                }
            }
            passwds.sort_by_key(|p| p.name.clone());

            if passwds.len() % 2 != 0 {
                // Added new because we're showing the list in two columns and need to be even
                passwds.push(PassModel{
                    name: String::new(),
                    ptype: String::new(),
                    desc: String::new(),
                    account: String::new(),
                    password: String::new(),
                    cypher: String::new(),
                    updated: 0.0,
                    expiration: 0.0,
                });
            }
        }
        Err(_) => {
            model.error = Some(format!("Can't get the list of passwords"));
        }
    }
}
