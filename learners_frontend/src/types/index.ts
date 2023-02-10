export default interface ITabObject {
  id: string;
  icon: string;
  tooltip: string;
  type: string;
  url: string;
  target?: string;
  admin?: boolean;
  badgevalue?: number;
}
