import React from "react";
import FormLabel from "@mui/material/FormLabel";
import Grid from "@mui/material/Grid2";
import OutlinedInput from "@mui/material/OutlinedInput";
import { styled } from "@mui/material/styles";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";

const FormGrid = styled(Grid)(() => ({
  display: "flex",
  flexDirection: "column",
}));

const EthnicityOptions = [
  { value: 1, label: "Mexican American" },
  { value: 2, label: "Other Hispanic" },
  { value: 3, label: "Non-Hispanic White" },
  { value: 4, label: "Non-Hispanic Black" },
  { value: 6, label: "Non-Hispanic Asian" },
  { value: 7, label: "Other Race - Including Multi-Racial" },
  { value: 8, label: "Indian" },
];

const GenderOptions = [
  { value: 0, label: "Female" },
  { value: 1, label: "Male" },
];

export default function PatientForm({ formData, setFormData }) {
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <Grid container spacing={3} sx={{ maxWidth: "600px", margin: "0 auto" }}>
      <FormGrid size={{ xs: 12 }}>
        <FormLabel htmlFor="patient-name">Patient name</FormLabel>
        <OutlinedInput
          id="PatientName"
          name="PatientName"
          type="text"
          placeholder="Sarah Smith"
          size="small"
          value={formData.PatientName}
          onChange={handleChange}
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel required htmlFor="Glucose">
          Glucose
        </FormLabel>
        <OutlinedInput
          id="Glucose"
          name="Glucose"
          type="number"
          placeholder="100"
          value={formData.Glucose}
          required
          size="small"
          onChange={handleChange}
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel required htmlFor="bmi">
          Body mass index
        </FormLabel>
        <OutlinedInput
          id="BMI"
          name="BMI"
          type="number"
          placeholder="30"
          value={formData.BMI}
          required
          size="small"
          onChange={handleChange}
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel required htmlFor="age">
          Age
        </FormLabel>
        <OutlinedInput
          id="Age"
          name="Age"
          type="number"
          placeholder="35"
          value={formData.Age}
          required
          size="small"
          onChange={handleChange}
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel required htmlFor="BloodPressure">
          Blood Pressure
        </FormLabel>
        <OutlinedInput
          id="BloodPressure"
          name="BloodPressure"
          type="number"
          placeholder="85"
          value={formData.BloodPressure}
          required
          size="small"
          onChange={handleChange}
        />
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel required htmlFor="Gender">
          Gender
        </FormLabel>
        <Select
          id="Gender"
          name="Gender"
          value={formData.Gender}
          onChange={handleChange}
          size="small"
        >
          {GenderOptions.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              {option.label}
            </MenuItem>
          ))}
        </Select>
      </FormGrid>
      <FormGrid size={{ xs: 12, md: 6 }}>
        <FormLabel required htmlFor="Ethnicity">
          Ethnicity
        </FormLabel>
        <Select
          id="Ethnicity"
          name="Ethnicity"
          value={formData.Ethnicity}
          onChange={handleChange}
          size="small"
        >
          {EthnicityOptions.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              {option.label}
            </MenuItem>
          ))}
        </Select>
      </FormGrid>
    </Grid>
  );
}
