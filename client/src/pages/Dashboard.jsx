import { useSelector } from 'react-redux';
import Permission from '../components/Permission';
import { PERMISSIONS } from '../utils/rbac';
import FileUpload from '../components/FileUpload/FileUpload';
import FileListing from '../components/FileListing';

const Dashboard = () => {
  const { auth } = useSelector(state => state);
  const { user } = auth;
  return (
    <div>
      <h3 style={{textAlign: 'center', marginBottom:10}}>Welcome, {user.full_name}!</h3>
      
      <Permission permissions={[PERMISSIONS.FILE_UPLOAD]}>
        <FileUpload />
      </Permission>
      <FileListing />
    </div>
  );
};

export default Dashboard;
