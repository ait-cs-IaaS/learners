export default interface ITabObject {
  id: string;
  icon: string;
  tooltip: string;
  _type: string;
  url: string;
  index?: number;
  openedInTab?: boolean;
}
