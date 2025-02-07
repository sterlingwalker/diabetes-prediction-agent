import React, { useState } from "react";
import FormLabel from "@mui/material/FormLabel";
import Grid from "@mui/material/Grid2";
import OutlinedInput from "@mui/material/OutlinedInput";
import { styled } from "@mui/material/styles";

const FormGrid = styled(Grid)(() => ({
  display: "flex",
  flexDirection: "column",
}));

export default function PatientForm({formData, setFormData}) {

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <Grid container spacing={3}>
      <FormGrid size={{ xs: 12 }}>
        <FormLabel htmlFor="patient-name">Patient name</FormLabel>
        <OutlinedInput
          id="patient-name"
          name="patient-name"
          type="name"
          placeholder="Sarah Smith"
          size="small"
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel htmlFor="Glucose">Glucose</FormLabel>
        <OutlinedInput
          id="Glucose"
          name="Glucose"
          type="Glucose"
          placeholder="100"
          required
          size="small"
          onChange={handleChange}
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel htmlFor="bmi">Body mass index</FormLabel>
        <OutlinedInput
          id="BMI"
          name="BMI"
          type="BMI"
          placeholder="30"
          required
          size="small"
          onChange={handleChange}
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel htmlFor="age">Age</FormLabel>
        <OutlinedInput
          id="Age"
          name="Age"
          type="Age"
          placeholder="35"
          required
          size="small"
          onChange={handleChange}
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel htmlFor="BloodPressure">Blood Pressure</FormLabel>
        <OutlinedInput
          id="BloodPressure"
          name="BloodPressure"
          type="BloodPressure"
          placeholder="85"
          required
          size="small"
          onChange={handleChange}
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel htmlFor="Insulin">Insulin</FormLabel>
        <OutlinedInput
          id="Insulin"
          name="Insulin"
          type="Insulin"
          placeholder="80"
          required
          size="small"
          onChange={handleChange}
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel htmlFor="Pregnancies">Pregnancies</FormLabel>
        <OutlinedInput
          id="Pregnancies"
          name="Pregnancies"
          type="Pregnancies"
          placeholder="1"
          required
          size="small"
          onChange={handleChange}
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel htmlFor="SkinThickness">Skin Thickness</FormLabel>
        <OutlinedInput
          id="SkinThickness"
          name="SkinThickness"
          type="SkinThickness"
          placeholder="0"
          required
          size="small"
          onChange={handleChange}
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel htmlFor="DiabetesPedigreeFunction">
          Diabetes Pedigree Value
        </FormLabel>
        <OutlinedInput
          id="DiabetesPedigreeFunction"
          name="DiabetesPedigreeFunction"
          type="DiabetesPedigreeFunction"
          placeholder="0"
          required
          size="small"
          onChange={handleChange}
        />
      </FormGrid>
    </Grid>
  );
}
