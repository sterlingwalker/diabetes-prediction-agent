import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import Snackbar, { SnackbarCloseReason } from "@mui/material/Snackbar";
import React from "react";
import CloseIcon from "@mui/icons-material/Close";
import Modal from "@mui/material/Modal";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

const style = {
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: "75%",
  bgcolor: "background.paper",
  boxShadow: 24,
  p: 4,
};

export default function TermsAndConditions() {
  const [open, setOpen] = React.useState(true);
  const [modalOpen, setModalOpen] = React.useState(false);

  const handleClose = (
    event: React.SyntheticEvent | Event,
    reason?: SnackbarCloseReason,
  ) => {
    if (reason === "clickaway") {
      return;
    }

    setOpen(false);
  };

  const handleOpenTerms = () => {
    setOpen(false);
    setModalOpen(true);
  };

  const handleModalClose = () => {
    setModalOpen(false);
  };

  const action = (
    <React.Fragment>
      <Button color="primary" size="small" onClick={handleOpenTerms}>
        TERMS
      </Button>
      <IconButton
        size="small"
        aria-label="close"
        color="inherit"
        onClick={handleClose}
      >
        <CloseIcon fontSize="small" />
      </IconButton>
    </React.Fragment>
  );

  return (
    <div>
      <Snackbar
        open={open}
        autoHideDuration={6000}
        onClose={handleClose}
        message="By using this application, you agree to the terms and conditions."
        action={action}
      />
      <Modal open={modalOpen} onClose={handleModalClose}>
        <Box sx={style}>
          <Typography id="modal-modal-title" variant="h6" component="h2">
            Disclaimer
          </Typography>
          <Typography id="modal-modal-description" sx={{ mt: 2 }}>
            This application is designed to provide educational information and
            predictive insights regarding diabetes risk based on user-provided
            data. It is not a substitute for professional medical diagnosis,
            advice, or treatment. The diabetes risk assessment and predictions
            provided by this app are based on general information and predictive
            algorithms and do not constitute a formal medical diagnosis.
            Consultation interactions provided through this app with virtual
            professionals (including dieticians, fitness trainers, and
            healthcare professionals) are intended solely for informational and
            educational purposes. They do not replace personalized medical
            advice, diagnosis, or treatment plans provided by qualified
            healthcare providers. Always consult with your healthcare provider
            or physician before making medical decisions or implementing changes
            to your health or fitness routine. If you believe you have symptoms
            indicative of diabetes or any other medical condition, immediately
            seek professional medical attention. Reliance on any information or
            resources provided by this app is at your own risk. The developers,
            creators, and partners associated with this application do not
            assume any liability or responsibility for adverse outcomes or
            damages arising from reliance on the information provided by the
            app, including the predictive results and consultations with virtual
            experts. By using this application, you acknowledge and accept the
            limitations and responsibilities outlined above.
          </Typography>
        </Box>
      </Modal>
    </div>
  );
}
