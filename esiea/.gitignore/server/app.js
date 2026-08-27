const express = require("express");
const cors = require("cors");
const axios = require("axios");
const dotenv = require("dotenv");
const { ConfidentialClientApplication } = require("@azure/msal-node");
const path = require("path");

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, "../")));

const {
  PORT,
  PBI_TENANT_ID,
  PBI_CLIENT_ID,
  PBI_CLIENT_SECRET,
  PBI_WORKSPACE_ID,
  PBI_REPORT_ID
} = process.env;

const authority = `https://login.microsoftonline.com/${PBI_TENANT_ID}`;

const msalConfig = {
  auth: {
    clientId: PBI_CLIENT_ID,
    authority,
    clientSecret: PBI_CLIENT_SECRET,
  },
};

const cca = new ConfidentialClientApplication(msalConfig);

async function getAadToken() {
  const result = await cca.acquireTokenByClientCredential({
    scopes: ["https://analysis.windows.net/powerbi/api/.default"],
  });

  if (!result || !result.accessToken) {
    throw new Error("Impossible d'obtenir le token AAD.");
  }

  return result.accessToken;
}

async function getReportInfo(accessToken) {
  const url = `https://api.powerbi.com/v1.0/myorg/groups/${PBI_WORKSPACE_ID}/reports/${PBI_REPORT_ID}`;

  const response = await axios.get(url, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return response.data;
}

async function generateEmbedToken(accessToken, reportId, datasetId) {
  const url = "https://api.powerbi.com/v1.0/myorg/GenerateToken";

  const body = {
    reports: [{ id: reportId }],
    datasets: [{ id: datasetId }],
    targetWorkspaces: [{ id: PBI_WORKSPACE_ID }],
  };

  const response = await axios.post(url, body, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
  });

  return response.data;
}

app.get("/api/powerbi/embed-info", async (req, res) => {
  try {
    const aadToken = await getAadToken();
    const report = await getReportInfo(aadToken);

    const embedToken = await generateEmbedToken(
      aadToken,
      report.id,
      report.datasetId
    );

    res.json({
      reportId: report.id,
      embedUrl: report.embedUrl,
      embedToken: embedToken.token,
      expiry: embedToken.expiration,
    });
  } catch (error) {
    console.error("Erreur embedding:", error.response?.data || error.message);

    res.status(500).json({
      error: "Erreur lors de la génération des informations d'intégration.",
      details: error.response?.data || error.message,
    });
  }
});

app.listen(PORT || 3000, () => {
  console.log(`Serveur lancé sur http://localhost:${PORT || 3000}`);
});