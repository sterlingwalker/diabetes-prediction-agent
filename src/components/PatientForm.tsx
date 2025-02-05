import * as React from "react";
import FormLabel from "@mui/material/FormLabel";
import Grid from "@mui/material/Grid2";
import OutlinedInput from "@mui/material/OutlinedInput";
import { styled } from "@mui/material/styles";

const FormGrid = styled(Grid)(() => ({
  display: "flex",
  flexDirection: "column",
}));

export default function PatientForm() {
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
        <FormLabel htmlFor="glucose">Glucose</FormLabel>
        <OutlinedInput
          id="glucose"
          name="glucose"
          type="glucose"
          placeholder="100"
          required
          size="small"
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel htmlFor="bmi">Body mass index</FormLabel>
        <OutlinedInput
          id="bmi"
          name="bmi"
          type="bmi"
          placeholder="30"
          required
          size="small"
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel htmlFor="age">Age</FormLabel>
        <OutlinedInput
          id="age"
          name="age"
          type="age"
          placeholder="35"
          required
          size="small"
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel htmlFor="bloodPressure">Blood Pressure</FormLabel>
        <OutlinedInput
          id="bloodPressure"
          name="bloodPressure"
          type="bloodPressure"
          placeholder="85"
          required
          size="small"
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel htmlFor="insulin">Insulin</FormLabel>
        <OutlinedInput
          id="insulin"
          name="insulin"
          type="insulin"
          placeholder="80"
          required
          size="small"
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel htmlFor="pregnancies">Pregnancies</FormLabel>
        <OutlinedInput
          id="pregnancies"
          name="pregnancies"
          type="pregnancies"
          placeholder="1"
          required
          size="small"
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel htmlFor="skinThickness">Skin Thickness</FormLabel>
        <OutlinedInput
          id="skinThickness"
          name="skinThickness"
          type="skinThickness"
          placeholder="0"
          required
          size="small"
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel htmlFor="diabetesPedigree">
          Diabetes Pedigree Value
        </FormLabel>
        <OutlinedInput
          id="diabetesPedigree"
          name="diabetesPedigree"
          type="diabetesPedigree"
          placeholder="0"
          required
          size="small"
        />
      </FormGrid>
    </Grid>
  );
}
