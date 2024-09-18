<template>
  <div class="row justify-evenly">
    <q-card class="column no-wrap" style="width: 49%; height: 100%; margin-right: 5px;">
      <div class="row" style="height: 100%;">
        <q-card-section style="width: 100%;">
          <q-card-section class="row justify-between" style="height: 5%">
            <div class="col-2"></div>
            <div class="text-h6 text-primary">Patient Search</div>
            <div class="col-2"></div>
          </q-card-section>
          <q-card-section class="q-pt-md" style="height: 75px">
            <div style="width: 100%" class="q-pa-sm">
              <div class="row no-wrap" style="width: 100%">
                <q-input
                  style="width: 100%"
                  rounded
                  outlined
                  dense
                  v-model="patientSearchText"
                  placeholder="Write a condition"
                  @keyup.enter="searchPatient"
                />
                <div class="q-px-sm"></div>
                <q-btn
                  :loading="loadingPatientSearch"
                  round
                  color="primary"
                  icon="search"
                  @click="searchPatient"
                />
              </div>
            </div>
          </q-card-section>
          <q-card-section class="row justify-between" style="height: 5%">
            <div class="col-2"></div>
            <div class="text-h6 text-primary">Search Results</div>
            <div class="col-2"></div>
          </q-card-section>
          <div
            class="q-pt-md"
            style="display: flex; justify-content: space-between; height: 80%;"
          >
            <div class="table-container" style="width: 100%; height: 100%;">
              <table>
                <tbody>
                  <tr v-if="combinedResults.length == 0">
                    <td class="empty-row">No results found</td>
                  </tr>
                  <tr
                    v-else
                    v-for="(row, index) in combinedResults"
                    :key="index"
                    :class="{ highlighted: selectedRow == index }"
                    @click="
                      selectRow(index);
                      attachCriteria(row);
                    "
                  >
                    <td v-html="row.context"></td>
                  </tr>
                  <tr
                    v-if="loadingPatientSearch || loadingCriteriaCheck"
                  >
                    <td colspan="1">
                      <q-inner-loading showing color="primary" />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </q-card-section>
      </div>
    </q-card>
    <div class="column no-wrap" style="width: 50%; height: 100%">
      <div class="row" style="height: 100%; width: 100%">
        <q-card style="width: 100%; height: 35%; margin-bottom: 5px;">
          <q-card-section class="row justify-between" style="height: 5%">
            <div class="col-2"></div>
            <div class="text-h6 text-primary">Inclusion/Exclusion Criteria</div>
            <div class="col-2"></div>
          </q-card-section>
          <q-card-section class="" style="height: 80%">
            <div style="width: 100%" class="q-pa-sm">
              <q-input
                style="width: 100%; max-height: 150px;"
                type="textarea"
                outlined
                dense
                v-model="criteriacheckText"
                placeholder="Inclusion-Exclusion Criteria"
                @keyup.enter="criteriaCheck"
              />
              <div class="q-px-sm"></div>
              <q-btn
                :loading="loadingCriteriaCheck"
                round
                color="primary"
                icon="search"
                @click="criteriaCheck"
              />
            </div>
          </q-card-section>
        </q-card>
        <q-card style="width: 100%; height: 64%;">
          <q-card-section class="row justify-between" style="height: 5%">
            <div class="col-2"></div>
            <div class="text-h6 text-primary">ChatBot Output</div>
            <div class="col-2"></div>
          </q-card-section>
          <q-card-section class="" style="height: 90%">
            <div
              v-if="loadingChatBot"
              class="column justify-center items-center no-wrap col-12"
              style="height: 100%"
            >
              <q-spinner color="primary" size="6em" />
            </div>
            <div
              v-if="!loadingChatBot"
              class="column justify-center items-center no-wrap col-12"
              style="height: 100%"
            >
              <div
                class="row justify-start items-center"
                style="width: 100%"
              ></div>
              <div
                style="
                  height: 100%;
                  width: 100%;
                  border-radius: 4px;
                  border: 1.5px solid #bdc3c7;
                "
                class="overflow-auto q-pa-md"
                ref="chatWindow"
              >
                <div class="q-px-sm row justify-center" style="height: 100%">
                  <div class="col-12">
                    <div
                      v-for="chatLine in chatHistory"
                      :key="chatLine"
                      :class="
                        'row justify-' +
                        chatConfig['chatLinePosition'][chatLine.role] +
                        ' q-py-sm'
                      "
                    >
                      <div
                        :class="
                          'bg-' +
                          chatConfig['chatLineColor'][chatLine.role] +
                          ' q-pa-sm'
                        "
                        style="
                          border-radius: 12px;
                          width: fit-content;
                          max-width: 60%;
                          white-space: pre-line;
                        "
                      >
                        {{ chatLine.content }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="q-pa-sm"></div>
              <div class="row justify-center no-wrap" style="width: 100%">
                <q-input
                  style="width: 100%"
                  rounded
                  outlined
                  dense
                  v-model="inputText"
                  placeholder="Write a message"
                  @keyup.enter="
                    loadingChatResponse ? true : sendMessage(inputText)
                  "
                />
                <div class="q-px-sm"></div>
                <q-btn
                  :loading="loadingChatResponse"
                  round
                  color="primary"
                  icon="send"
                  @click="sendMessage(inputText)"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </div>
</template>

<style>
.table-container {
  position: relative;
  max-height: 510px; 
  overflow-y: auto; 
  border: 1px solid #b9b9b9; 
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); 
}
table {
  width: 100%;
  height: 100%;
  border-collapse: collapse; 
  position: relative;
}
td {
  border-top: 1px solid #ddd;
  border-bottom: 1px solid #ddd;
  padding: 8px;
}
tr:first-child td {
  border-top: none; 
}
tr:last-child td {
  border-bottom: none;
}
tr.highlighted {
  background-color: #f0f0f0;
}
tr:hover {
  background-color: #f5f5f5;
  cursor: pointer;
}
.empty-row {
  height: 100%;
  text-align: center; 
  vertical-align: middle; 
  color: #999;
}
</style>

<script>
import { defineComponent, ref } from "vue";
import { api, llamaServer, patientSearchApi } from "boot/axios";

const patientColumns = [
  {
    name: "context",
    label: "",
    field: "context",
    required: true,
    sortable: false,
    align: "left",
  },
];

const patientColumns1 = [
  {
    name: "inclusion",
    label: "inclusion",
    field: "text",
    required: true,
    sortable: false,
    align: "left",
  },
];

const visiblePatientColumns = [
  "document_id",
  "context",
];
const visiblePatientColumns1 = ["inclusion"];
const chatConfig = {
  chatLineColor: {
    assistant: "purple-4",
    user: "teal-4",
  },
  chatLinePosition: {
    assistant: "begin",
    user: "end",
  },
};

const chatPrompts = {
  assistente: [
    {
      role: "system",
      content:
        "Questa è una conversazione tra un utente umano e un assistente artificiale esperto di medicina. L'assistente è empatico ed educato. L'assistente parla in italiano e risponde alle domande in italiano. L'assistente è qui per rispondere alle domande, fornire consigli e aiutare l'utente a prendere decisioni. L'assistente è tenuto a rispondere a domande o task riguardanti i testi clinici al meglio delle sue possibilità.  Le risposte sono coincise ed esaustive.",
    },
  ],
};

const initChatHistory = {
  default: [
    {
      content: "Ciao sono il tuo assistente come posso aiutarti?",
      role: "assistant",
    },
  ],
};

export default defineComponent({
  name: "ChatBot",
  props: {
    inputLetter: {
      type: String,
      required: true,
    },
    inputMode: {
      type: String,
      required: true,
    },
  },
  emits: ["update:inputMode", "update:inputLetter"],
  data() {
    return {
      selectedRow: null,
      inputText: ref(""),
      chatPrompts,
      initChatHistory,
      loadingChatBot: ref(false),
      loadingChatResponse: ref(false),
      chatConfig,
      chatHistory: ref(JSON.parse(JSON.stringify(initChatHistory["default"]))),
      visiblePatientColumns,
      visiblePatientColumns1,
      patientColumns,
      patientColumns1,
      loadingPatientSearch: ref(false),
      patientSearchText: ref(""),
      patientResults: ref([]),
      loadingCriteriaCheck: ref(false),
      criteriacheckText: ref(""),
      criteriaResults: ref([]),
      inputModeLocal: "edit",
      inputLetterLocal: "",
    };
  },
  computed: {
    combinedResults() {
      const combined = [];
      const maxLength = 100; // Adjust this value to your desired length

      function truncateText(text, maxLength) {
        if (text.length <= maxLength) {
          return text;
        }
        return text.substring(0, maxLength) + "...";
      }

      this.patientResults.forEach((result, index) => {
        const row = {};
        let idString = `<strong>PatientID</strong>: ${result.document_id}`;
        let truncatedText = truncateText(result.text, maxLength);
        let contextString = `<strong>Context</strong>: ${truncatedText}`;
        row.context = `${idString}<br>${contextString}`;
        row.text = this.patientResults[index].text;
        if (this.criteriaResults[index]) {
          let inclusionString = `<strong>Elegiblity</strong>: ${this.criteriaResults[index].text}`;
          row.context = `${idString}<br>${contextString}<br>${inclusionString}`;
          row.inclusion = this.criteriaResults[index].text;
        }
        combined.push(row);
      });
      return combined;
    },
  },
  methods: {
    async sendMessage(myText) {
      let currentChat = [{ content: myText, role: "user" }];

      this.loadingChatResponse = true;
      this.$refs.chatWindow.scrollTop = this.$refs.chatWindow.scrollHeight;
      if (myText === "") return;
      this.chatHistory = this.chatHistory.concat(currentChat);
      this.inputText = "";
      this.chatHistory.push({
        content: "...",
        role: "assistant",
      });
      this.$nextTick(() => {
        this.$refs.chatWindow.scrollTop = this.$refs.chatWindow.scrollHeight;
      });
      fetch(llamaServer + "/v1/chat/completions", {
        // fetch('http://localhost:51124/v1/chat/completions', {
        method: "POST",
        body: JSON.stringify({
          messages: this.chatPrompts["assistente"].concat(this.chatHistory),
          stream: true,
          temperature: 0,
          max_tokens: 500,
        }),
        headers: {
          "Content-Type": "application/json",
          timeout: 36000,
        },
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Errore nella chiamata POST");
          }
          return response.body;
        })
        .then((body) => {
          const reader = body.getReader();
          const processStream = ({ done, value }) => {
            if (done) {
              console.log("Stream di eventi completato");
              this.loadingChatResponse = false;
              return;
            }
            let chunkRaw = new TextDecoder().decode(value);
            const chunkArray = chunkRaw.split("data:").slice(1);

            for (let chunk of chunkArray) {
              try {
                chunk = JSON.parse(chunk.split(": ping -")[0]);
              } catch {
                console.log("il parsing non è andato a buon fine");
                console.log(chunk);
              }
              if (Object.keys(chunk).includes("choices")) {
                if (
                  Object.keys(chunk["choices"][0]["delta"]).includes("role")
                ) {
                  this.chatHistory.slice(-1)[0]["role"] =
                    chunk["choices"][0]["delta"]["role"];
                  this.chatHistory.slice(-1)[0]["content"] = "";
                } else {
                  this.chatHistory.slice(-1)[0]["content"] += chunk[
                    "choices"
                  ][0]["delta"]["content"]
                    ? chunk["choices"][0]["delta"]["content"]
                    : "";
                  this.$nextTick(() => {
                    this.$refs.chatWindow.scrollTop =
                      this.$refs.chatWindow.scrollHeight;
                  });
                }
              }
            }
            return reader.read().then(processStream);
          };

          reader.read().then(processStream);
        })
        .catch((error) => {
          this.chatHistory.slice(-1)[0]["content"] =
            "Si è verificato un errore controlla che il testo non sia troppo lungo";
          console.error(
            "Si è verificato un errore durante la chiamata POST:",
            error
          );
          this.loadingChatResponse = false;
        });
    },

    loadChatBot() {
      this.resetChatHistory();
    },

    resetChatHistory() {
      this.chatHistory = JSON.parse(
        JSON.stringify(this.initChatHistory["default"])
      );
    },

    attachDocument() {
      if (this.inputLetter != null && this.inputLetter != "")
        this.attachedDocument = this.inputLetter;
      this.chatHistory.push({
        content:
          "Rispondi alle domande relative al seguente Testo Clinico: ```" +
          this.attachedDocument +
          "```",
        role: "user",
        visible: false,
      });
      this.loadingChatResponse = true;
      fetch(llamaServer + "/v1/chat/completions", {
        // fetch('http://131.175.15.22:61111/hbd-demo-api/send_message/', {
        method: "POST",
        body: JSON.stringify({
          messages: this.chatPrompts["assistente"].concat(this.chatHistory),
          stream: true,
          temperature: 0,
          max_tokens: 1,
        }),
        headers: {
          "Content-Type": "application/json",
          timeout: 36000,
        },
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Errore nella chiamata POST");
          }
          return response.body;
        })
        .then((body) => {
          const reader = body.getReader();
          const processStream = ({ done, value }) => {
            if (done) {
              console.log("Caricamento allegato completato");
              this.loadingChatResponse = false;
              return;
            }
            return reader.read().then(processStream);
          };
          reader.read().then(processStream);
        });
    },

    selectRow(index) {
      this.selectedRow = index; // Set selectedRow to index of clicked row
    },

    attachCriteria(row) {
      console.log("attach called with:", row);
      const txt = row.text;
      this.$emit("update:inputLetter", txt);
      this.$emit("update:inputMode", "edit");
      this.dropzoneURL = "";
      this.resetChatHistory();
      const text = this.criteriacheckText;
      if (text != null && text.trim() !== "") {
        const criteriaText = text.trim();
        const criteriaResult = row.inclusion.trim();
        const CriteriaMessage = `Given the clinical text:
              (${txt})
              and the following eligibility inclusion criteria for a clinical trial:
              (${criteriaText})
              Determined the patient:
              (${criteriaResult})`;
        this.chatHistory.push({ content: CriteriaMessage, role: "user" });
      } else {
        this.chatHistory.push({
          content:
            "Rispondi alle domande relative al seguente Testo Clinico: ```" +
            txt +
            "```",
          role: "user",
        });
      }

      this.loadingChatResponse = true;
      fetch(llamaHost + "/v1/chat/completions", {
        // fetch('http://131.175.15.22:61111/hbd-demo-api/send_message/', {
        method: "POST",
        body: JSON.stringify({
          messages: this.chatPrompts["assistente"].concat(this.chatHistory),
          stream: true,
          temperature: 0,
          max_tokens: 1,
        }),
        headers: {
          "Content-Type": "application/json",
          timeout: 36000,
        },
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Errore nella chiamata POST");
          }
          return response.body;
        })
        .then((body) => {
          const reader = body.getReader();
          const processStream = ({ done, value }) => {
            if (done) {
              console.log("Caricamento allegato completato");
              this.loadingChatResponse = false;
              return;
            }
            return reader.read().then(processStream);
          };
          reader.read().then(processStream);
        });
    },

    searchPatient() {
      this.loadingPatientSearch = true;
      patientSearchApi
        .post("/patient_search", { query: this.patientSearchText })
        .then((response) => {
          console.log(response.data);
          this.loadingPatientSearch = false;
          this.patientResults = response.data.output;
        })
        .catch((error) => {
          console.log("error with patient search call:", error.message);
          this.loadingPatientSearch = false;
        });
      this.criteriaResults = [];
    },

    criteriaCheck() {
      this.loadingCriteriaCheck = true;
      patientSearchApi
        .post("/criteria_check", { criteria: this.criteriacheckText })
        .then((response) => {
          console.log(response.data);
          this.loadingCriteriaCheck = false;
          this.criteriaResults = response.data.criteria;
        })
        .catch((error) => {
          console.log("error with criteria check:", error.message);
          this.loadingCriteriaCheck = false;
        });
    },

    showRetrievedDocument(text) {
      this.$emit("update:inputLetter", text);
      this.$emit("update:inputMode", "edit");
      this.dropzoneURL = "";
    },

    updateTaskName() {
      this.setupName = null;
      this.taskName = this.taskName.value;
    },
  },
});
</script>
