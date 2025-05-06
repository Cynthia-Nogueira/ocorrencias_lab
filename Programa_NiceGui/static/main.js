// Grid API: Access to Grid API methods
let gridApi;

// Row Data Interface

const gridOptions = {
  defaultColDef: {
    flex: 10,
  },
  // Data to be displayed
  rowData: [],
  // Columns to be displayed (Should match rowData properties)
  columnDefs: [
    {
      field: "actions",
      headerName: "Actions",
    },
  ],
};

// setup the grid after the page has finished loading
document.addEventListener("DOMContentLoaded", () => {
  const gridDiv = document.querySelector("#myGrid");
  gridApi = agGrid.createGrid(gridDiv, gridOptions);

  fetch("https://www.ag-grid.com/example-assets/small-company-data.json")
    .then((response) => response.json())
    .then((data) => {
      gridApi.setGridOption("rowData", data);
    });
});

#----------------------- FILTROS --------------------------

const socket = new WebSocket("ws://localhost:8000/ws");

socket.onopen = function() {
    console.log("Conectado ao WebSocket");
};

socket.onmessage = function(event) {
    console.log("Mensagem recebida: ", event.data);
};


