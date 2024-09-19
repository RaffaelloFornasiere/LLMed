<template>

<div v-if="useLargerScreen"
  class="q-pa-md text-h4 text-center text-weight-bold" style="height: 100%"
>
  Application is not supported on smaller screens.
  <br>
  <span
  class="text-h6"
  >(Minimum screen size: 1024x768)
  </span>
</div>
  <q-page
    v-if="!useLargerScreen"
    padding class="row items-stretch" style="height: 100%; min-width: 1024px">
    <div class="col-12 column no-wrap">
      <div class="row no-wrap justify-between" style="height: 100%">
        <div class="column no-wrap full-height full-width">
          <resizable-drawer
direction="row"
          >
            <template v-slot:block1>
              <input-document
                v-model:input-letter="inputLetter"
              ></input-document>
            </template>
            <template v-slot:block2>
              <medical-information-extraction
                v-model:doc="inputLetter"
                style="height: 100%"
                ref="medicalInformationExtractionComponent"
              ></medical-information-extraction>
            </template>
          </resizable-drawer>

        </div>
      </div>
    </div>
  </q-page>
</template>

<script>
import { defineComponent, ref } from "vue";
import MedicalInformationExtraction from "components/MedicalInformationExtraction/MedicalInformationExtraction.vue";
import DeidentificationClassic from "components/DeidentificationClassic.vue";
import PharmacologicalEventExtraction from "components/PharmacologicalEventExtraction.vue";
import ChatBot from "components/ChatBot.vue";
import QuestionAnswering from "components/QuestionAnswering.vue";
import PatientSearch from "components/PatientSearch.vue";
import MIEChat from "components/MedicalInformationExtraction/MIEChat.vue";
import ResizableDrawer from "src/utils/ResizableDrawer.vue";
import InputDocument from "components/InputDocument.vue";

export default defineComponent({
  name: "Health Big Data WG1 Demo",
  components: {
    InputDocument,
    ResizableDrawer,
    MedicalInformationExtraction,
  },

  setup() {
    return {
      useLargerScreen: ref(false),
      modelName: ref(""),
      inputMode: ref("edit"),
      dropzoneURL: ref(""),
      dropzoneURL2: ref(""),
      highlightColor: ref(false),
      saliencyMap: ref([]),
      loadingSaliencyMap: ref(false),
      inputLetter: ref(),
      letterNames: ref([]),
      letterDict: ref({}),
      taskName: ref(""),
      taskNames: ref([
        "deidentification",
        "pharmacological event extraction",
        "question answering (extractive)",
        "question answering (generative)",
        "patient cohort search TODO",
        "Medical Information Extraction",
      ]),
      taskOptionGroups: [
        {
          label: "Information Extraction with LLM",
          value: "Information Extraction with LLM",
          setupNames: ["Medication & Timeline"],
        }
      ],
      setupName: ref(""),
      modelConfig: ref({
        "Track1 n2c2 Challenge (en)": {
          modelName: "track1 n2c2 pipeline1",
          lang: "en",
          modelType: "t5-ner",
          drug: {
            modelName: "simplet5-epoch-6-train-loss-0.2724-val-loss-0.1477",
            lang: "en",
            modelType: "t5-ner",
          },
          disposition: {
            modelName: "Bio_ClinicalBERT_model_trained_disposition-type",
            lang: "en",
            modelType: "bert-dee",
          },
          action: {
            modelName: "Bio_ClinicalBERT_model_trained_Action",
            lang: "en",
            modelType: "bert-dee",
          },
          negation: {
            modelName: "Bio_ClinicalBERT_model_trained_Negation",
            lang: "en",
            modelType: "bert-dee",
          },
          temporality: {
            modelName: "Bio_ClinicalBERT_model_trained_Temporality",
            lang: "en",
            modelType: "bert-dee",
          },
          actor: {
            modelName: "Bio_ClinicalBERT_model_trained_Actor",
            lang: "en",
            modelType: "bert-dee",
          },
          certainty: {
            modelName: "Bio_ClinicalBERT_model_trained_Certainty",
            lang: "en",
            modelType: "bert-dee",
          },
        },
        "Extractive: Roberta-large (multilingual)": {
          modelName: "deepset/xlm-roberta-large-squad2",
          lang: "it",
          modelType: "roberta-qa",
          thresold: 0.0,
        },
        "Extractive: BioBIT Italian": {
          modelName: "data/checkpoints/medBIT-r3-plus_75",
          lang: "it",
          modelType: "roberta-qa",
          thresold: 0.0,
        },
        "Translation-based: it->en, t5-base (english)": {
          modelName: "valhalla/t5-base-qa-qg-hl",
          lang: "en",
          modelType: "t5-qa",
          thresold: 0.6,
        },
        "Generative: t5-base (multilingual)": {
          modelName: "Narrativa/mT5-base-finetuned-tydiQA-xqa",
          lang: "it",
          modelType: "t5-qa",
          thresold: 0.6,
        },
        "mistral-7b-openorca-q5": {
          modelName: "mistral-7b-openorca-q5.ggmlv3.q4_1.bin",
        },
      }),
    };
  },
  mounted() {
    this.onResize()
    this.$nextTick(() => {
      window.addEventListener('resize', this.onResize);
    })
  },
  methods: {
    updateTaskName() {
      this.setupName = null;
      this.taskName = this.taskName.value;
    },
    onResize() {
      this.useLargerScreen = window.innerWidth < 1024 || window.innerHeight < 768;
    },
  },
});
</script>
