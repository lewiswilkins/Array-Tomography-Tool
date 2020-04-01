import React from "react";
import styled from "styled-components";
import colors from "../config/colors";

const Container = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  width: 100%;
  height: 100vh;
  background-color: ${colors.background};
`;

const Layout: React.FC = ({ children }) => <Container>{children}</Container>;

export default Layout;
