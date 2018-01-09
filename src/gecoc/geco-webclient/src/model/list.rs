#[derive(Serialize, Deserialize)]
pub struct PassModel {
    pub name: String,
    pub ptype: String,
    pub desc: Option<String>,
    pub account: Option<String>,
    pub password: String,
    pub cypher: String,
    pub updated: f64,
    pub expiration: f64,
}

impl PassModel {
}

#[derive(Serialize, Deserialize)]
pub struct ListModel {
    pub passwords: Vec<PassModel>,
}

impl ListModel {
    pub fn new() -> ListModel {
        ListModel {
            passwords: vec![],
        }
    }
}
