import * as React from "react";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import Paper from "@mui/material/Paper";
import ReactMarkdown from "react-markdown";
import DOMPurify from "dompurify";
import "../App.css";

function MarkdownRenderer({ content }) {
  if (!content) return null;

  const sanitizedContent = DOMPurify.sanitize(content);

  return (
    <ReactMarkdown
      components={{
        p: ({ node, ...props }) => (
          <Typography
            variant="body2"
            sx={{
              textAlign: "justify",
              marginBottom: "6px",
              whiteSpace: "pre-wrap",
            }}
            {...props}
          />
        ),
        ol: ({ node, ...props }) => (
          <ol
            style={{
              textAlign: "left",
              margin: "0",
              paddingLeft: "24px",
              lineHeight: "1.6",
            }}
            {...props}
          />
        ),
        ul: ({ node, ...props }) => (
          <ul
            style={{
              textAlign: "left",
              margin: "0",
              paddingLeft: "24px",
              lineHeight: "1.6",
            }}
            {...props}
          />
        ),
        li: ({ node, ...props }) => (
          <li style={{ textAlign: "left", marginBottom: "4px" }} {...props} />
        ),
        h1: ({ node, ...props }) => (
          <Typography
            variant="body1"
            sx={{
              fontWeight: "bold",
              textAlign: "left",
              marginBottom: "6px",
              color: "#2C3E50",
            }}
            {...props}
          />
        ),
        h2: ({ node, ...props }) => (
          <Typography
            variant="body1"
            sx={{
              fontWeight: "bold",
              textAlign: "left",
              marginBottom: "6px",
              color: "#34495E",
            }}
            {...props}
          />
        ),
        h3: ({ node, ...props }) => (
          <Typography
            variant="body2"
            sx={{
              fontWeight: "bold",
              textAlign: "left",
              marginBottom: "6px",
              color: "#5D6D7E",
            }}
            {...props}
          />
        ),
        hr: () => <Divider sx={{ margin: "12px 0" }} />,
      }}
    >
      {sanitizedContent}
    </ReactMarkdown>
  );
}

export default function Review({ response }) {
  return (
    <Paper
      elevation={3}
      sx={{ padding: "24px", backgroundColor: "#FAFAFA", borderRadius: "8px" }}
    >
      <Typography
        sx={{
          fontWeight: "bold",
          fontSize: "22px",
          marginBottom: "16px",
          textAlign: "left",
          color: "#2C3E50",
        }}
        variant="h6"
      >
        Medical Report - Patient Treatment Plan
      </Typography>
      <Divider sx={{ marginBottom: "16px" }} />
      <Grid container sx={{ textAlign: "left" }}>
        {[
          {
            title: "Endocrinologist's Recommendations",
            content: response?.endocrinologistRecommendation,
          },
          {
            title: "Dietitian's Meal Plan",
            content: response?.dietitianRecommendation,
          },
          {
            title: "Fitness Trainer's Plan",
            content: response?.fitnessRecommendation,
          },
          {
            title: "Overall Recommendation",
            content: response?.finalRecommendation,
          },
        ].map((item, index) => (
          <React.Fragment key={index}>
            <Stack
              direction="column"
              spacing={1}
              sx={{
                width: "100%",
                mb: 4,
                padding: "16px",
                backgroundColor: "#FFFFFF",
                borderRadius: "6px",
              }}
            >
              <Typography
                variant="body1"
                sx={{
                  fontWeight: "bold",
                  fontSize: "18px",
                  color: "#34495E",
                  textAlign: "left",
                  borderBottom: "2px solid #D5DBDB",
                  paddingBottom: "4px",
                  marginBottom: "8px",
                }}
              >
                {item.title}
              </Typography>
              <MarkdownRenderer content={item.content} />
            </Stack>
          </React.Fragment>
        ))}
      </Grid>
    </Paper>
  );
}
