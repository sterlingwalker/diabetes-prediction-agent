import * as React from 'react';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import Typography from '@mui/material/Typography';

const services = [
  {
    name: 'Diagnosis',
    desc: 'Calculated risk of developing diabetes',
    additional: '',
  },
  {
    name: 'Endocrinologist Recommendation',
    desc: 'Consultation with a specialist',
    additional: '',
  },
  {
    name: 'Dietician Recommendation',
    desc: 'Provide a custom diet plan to mitigate risk',
    additional: '',
  },
  {
    name: 'Fitness Trainer Recommendation',
    desc: 'Provide a custom fitness plan to mitigate risk',
    additional: '',
  },
];

export default function Info() {
  return (
    <React.Fragment>
      <List disablePadding>
        {services.map((service) => (
          <ListItem key={service.name} sx={{ py: 1, px: 0 }}>
            <ListItemText
              sx={{ mr: 2 }}
              primary={service.name}
              secondary={service.desc}
            />
            <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
              {service.additional}
            </Typography>
          </ListItem>
        ))}
      </List>
    </React.Fragment>
  );
}
