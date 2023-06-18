<template>
  <div class="sensor w-100">
    <b-container fluid class="text-left">
      <b-icon
        v-if="!autopilotView"
        :id="this.name + '-delecte-icon'"
        style="float: right"
        icon="trash-fill"
        font-scale="1.75"
        @click="deleteSensor()"
      ></b-icon>

      <h1 v-if="!autopilotView">{{ this.name }}</h1>
      <p class="mb-4" v-if="!autopilotView">
        {{ this.type }} ({{ this.info.category }})
      </p>

      <b-row>
        <div :id="name + '-settings-column'" class="col-xl-6">
          <div :id="name + '-general-settings-column'">
            <h4>General Settings</h4>
            <b-collapse visible :id="this.name + '-collapse-sensor'">
              <GnssSettings
                v-if="this.type === 'gnss'"
                :sensorName="this.name"
                :settings="this.settings"
                :url="this.sensorUrl"
              />
              <ImuSettings
                v-else-if="this.type === 'imu'"
                :sensorName="this.name"
                :settings="this.settings"
                :url="this.sensorUrl"
              />
              <CameraSettings
                v-else-if="this.type === 'camera'"
                :sensorName="this.name"
                :settings="this.settings"
                :url="this.sensorUrl"
              />
              <TachometerSettings
                v-else-if="this.type === 'tachometer'"
                :sensorName="this.name"
                :settings="this.settings"
                :url="this.sensorUrl"
              />
            </b-collapse>
          </div>
          <div :id="name + '-attack-settings-column'">
            <h4>Attack Settings</h4>
            <b-collapse visible :id="this.name + '-collapse-attack'">
              <GnssAttackSettings
                v-if="this.type === 'gnss'"
                :sensorName="this.name"
                :attackEngine="this.attackEngine"
                :url="this.sensorUrl"
              />
              <ImuAttackSettings
                v-else-if="this.type === 'imu'"
                :sensorName="this.name"
                :attackEngine="this.attackEngine"
                :url="this.sensorUrl"
              />
              <TachometerAttackSettings
                v-else-if="this.type === 'tachometer'"
                :sensorName="this.name"
                :attackEngine="this.attackEngine"
                :url="this.sensorUrl"
              />
              <AttackSettings
                v-else
                :sensorName="this.name"
                :attackEngine="this.attackEngine"
                :url="this.sensorUrl"
              />
            </b-collapse>
          </div>
        </div>
        <div v-if="!autopilotView" class="col-xl-6">
          <h4>Sensor Data</h4>
          <b-collapse visible :id="this.name + '-collapse-display'">
            <ImageDisplay
              v-if="this.type === 'camera'"
              :sensorName="this.name"
            />
            <TextDisplay v-else :dataType="this.type" :sensorName="this.name" />
          </b-collapse>
        </div>
      </b-row>
    </b-container>
  </div>
</template>

<script>
// @ is an alias to /src
import axios from "axios";

import GnssSettings from "@/components/GnssSettings.vue";
import ImuSettings from "@/components/ImuSettings.vue";
import CameraSettings from "@/components/CameraSettings.vue";
import TachometerSettings from "@/components/TachometerSettings.vue";

import AttackSettings from "@/components/AttackSettings.vue";
import GnssAttackSettings from "@/components/GnssAttackSettings.vue";
import ImuAttackSettings from "@/components/ImuAttackSettings.vue";
import TachometerAttackSettings from "@/components/TachometerAttackSettings.vue";

import TextDisplay from "@/components/TextDisplay";
import ImageDisplay from "@/components/ImageDisplay";

export default {
  name: "Sensor",
  components: {
    GnssSettings,
    ImuSettings,
    CameraSettings,
    TachometerSettings,
    AttackSettings,
    GnssAttackSettings,
    ImuAttackSettings,
    TachometerAttackSettings,
    TextDisplay,
    ImageDisplay,
  },
  props: {
    name: String,
    type: String,
    autopilotView: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    sensorUrl() {
      return (
        this.$store.state.simutackAddress +
        "/sensor/" +
        this.type +
        "/" +
        this.name
      );
    },
    // dataUrl: String,
  },
  data() {
    return {
      info: {
        name: "",
        type: "",
        category: "",
      },
      settings: null,
      attackEngine: null,
      subscription: null,
    };
  },
  mounted() {
    // Use full width if display in autopilot view
    if (this.autopilotView) {
      // Use nextTick to ensure all child components are properly setup
      this.$nextTick(function () {
        let settings = document.getElementById(this.name + "-settings-column");
        settings.classList.remove("col-xl-6");
        settings.classList.add("w-100");
        settings.classList.add("row");
        let generalSettings = document.getElementById(
          this.name + "-general-settings-column"
        );
        generalSettings.classList.add("col-xl-6");
        let attackSettings = document.getElementById(
          this.name + "-attack-settings-column"
        );
        attackSettings.classList.add("col-xl-6");
        // h4 -> h5

        let labels = settings.getElementsByClassName("col-form-label");
        // console.log(labels);
        // console.log(labels.length);
        // Loop through backwards in case the element gets removed from collection
        for (let i = labels.length - 1; i >= 0; i--) {
          let list = labels[i].classList;
          //   console.log(list);
          list.add("col-form-label-sm");
        }
        let inputs = settings.getElementsByClassName("form-control");
        //      console.log(inputs);
        for (let i = inputs.length - 1; i >= 0; i--) {
          // Loop through backwards in case the element gets removed from collection
          inputs[i].classList.add("form-control-sm");
        }
      });
    }

    axios({ method: "GET", url: this.sensorUrl }).then(
      (result) => {
        // console.log("Sensor data: ", result.data);
        this.info = result.data.info;
        this.settings = result.data.settings;
        this.attackEngine = result.data.attackEngine;
        this.subscription = result.data.subscription;
      },
      (error) => {
        console.error(error);
      }
    );
  },
  methods: {
    deleteSensor() {
      // Emit signal to parent to invoke deletion
      this.$emit("delete");
    },
  },
};
</script>
