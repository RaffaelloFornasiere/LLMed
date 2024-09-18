import { boot } from "quasar/wrappers";
import axios from "axios";

const patientSearch = './patient-search-api'
const patientSearchApi = axios.create({
  baseURL: patientSearch
})
const llamaServer = "./llama-server";
const baseApi = axios.create()
const api = axios.create({
  baseURL: "./api/",
});
export default boot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api
  app.config.globalProperties.$axios = axios;
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api;
});

export { axios, api, llamaServer, baseApi,patientSearchApi };
