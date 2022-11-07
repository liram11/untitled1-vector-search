import styled from 'styled-components'


export const Root = styled.div`
  position: relative;
`

interface Props {
  height?: number
}

export const TextArea = styled.textarea<Props>`
  border: none;
  overflow: auto;
  outline: none;

  resize: none;

  width: 100%;
  height: ${({height = 80}) => height}px;
  border-radius: 4px;
  padding: 12px 16px;


  box-shadow: rgb(0 0 0 / 20%) 0px 2px 6px 0px, rgb(0 0 0 / 14%) 0px 1px 1px 0px, rgb(0 0 0 / 12%) 0px 1px 3px 0px;

  &::placeholder {
    color: #aaa;
  }
`


export const ClearButton = styled.div`
  position: absolute;
  width: 40px;
  height: 40px;
  padding: 8px;
  right: 0;
  top: calc(50% - 20px);

  cursor: pointer;

  display: flex;

  flex-direction: column;  /* make main axis vertical */
  justify-content: center; /* center items vertically, in this case */
  align-items: center;
`
