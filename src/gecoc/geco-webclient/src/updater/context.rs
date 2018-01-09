use yew::html::App;
use yew::format::Json;
use yew::services::console::ConsoleService;
use yew::services::fetch::FetchService;
use yew::services::storage::{StorageService, Scope};
use yew::services::fetch::Method;

use serde_json::Value as JsonValue;

use updater::msg::Msg;
use updater::msg::BASE;

use model::Model;

pub const KEY: &'static str = "geco.model";

pub struct Context {
    pub console: ConsoleService,
    pub web: FetchService<Msg>,
    pub storage: StorageService,
}

impl Context {
    pub fn new(app: &mut App<Msg>) -> Context {
        Context {
            console: ConsoleService,
            web: FetchService::new(app.sender()),
            storage: StorageService::new(Scope::Local),
        }
    }

    pub fn get_model(&mut self) -> Model {
        let mut model;
        if let Json(Ok(restored_model)) = self.storage.restore(KEY) {
            model = restored_model;
        } else {
            model = Model::new();
        }

        model.login.token = None;
        model.list.passwords = vec![];

        model
    }

    pub fn post<F>(&mut self, path: &str, data: JsonValue, cb: F)
        where F: Fn(Result<JsonValue, ()>) -> Msg + 'static {

        self.web.fetch(Method::Post,
                      &format!("{}/{}", BASE, path),
                      Json(&data),
                      move |Json(data)| cb(data));
    }

    pub fn log(&mut self, msg: &str) {
        self.console.log(msg);
    }
}
