describe("st.set_page_config", () => {
  before(() => {
    cy.loadApp("http://localhost:3000/");
  });

  it("sets the page favicon with ico file", () => {
    cy.get("link[rel='shortcut icon']")
      .should("have.attr", "href")
      .should(
        "contain",
        "92018b2805266c4cb9a98e90c849ce5b5e7ba6d1af423bd7b7c345da.png"
      );
  });
});
