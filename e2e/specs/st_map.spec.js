describe("st.map", () => {
  before(() => {
    cy.loadApp("http://localhost:3000/");
  });

  it("displays 3 maps", () => {
    cy.get(".element-container .stDeckGlJsonChart").should("have.length", 3);
  });
});
