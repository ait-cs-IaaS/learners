import axios from "axios";
import { store } from "@/store";

// TODO: Change localhost
axios.defaults.baseURL = process.env.VUE_APP_API || "http://localhost:5000/";

let token = store.getters.getJwt;
if (token) axios.defaults.headers.common["Authorization"] = "Bearer " + token;
