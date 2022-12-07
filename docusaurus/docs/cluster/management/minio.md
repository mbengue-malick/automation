---
title: MinIO
---

## Keycloak policies

### Configure Keycloak Realm

All the following instructions take place in Keycloak admin interface. Adapted from [MinIO documentation](https://github.com/minio/minio/blob/master/docs/sts/keycloak.md).

- Go to Clients

  - Click on `minio-storage` (or create one)
    - Settings
    - Change `Access Type` to `confidential`.
    - Save
  - Click on Credentials tab
    - Copy the `Secret` to clipboard.
    - This value is needed for `MINIO_IDENTITY_OPENID_CLIENT_SECRET` for MinIO.
  - Click on Mappers tab
    - Create
      - `Name` with any text
      - `Mapper Type` is `User Client Role`
      - `Token Claim Name` is `policy`
      - `Claim JSON Type` is `string`
    - Save

### Configure users roles

- Go to Groups
  - Click New
  - Set a Name
  - Click on Role Mappings tab
  - In Client Roles, select `minio-storage` and assign the role you want the Users within this Group to have
- Go to Users
  - Click on a user
  - Click on the Groups tab
  - Join the Group you want this User to inherit the role(s) from

Then, on MinIO, create policies with the same name as the roles you created to map them through the `policy` User claim.

:::info
A list of the MinIO's built-in policies can be found [here](https://docs.min.io/minio/baremetal/security/minio-identity-management/policy-based-access-control.html)
:::

## Policies management

As a console admin, you can connect to MinIO and manage policies from the Access menu.

Example of a policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation",
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": ["arn:aws:s3:::mybucket/*"]
    },
    {
      "Effect": "Deny",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::otherbucket/*"]
    }
    {
      "Effect": "Deny",
      "Action": ["s3:ListAllMyBuckets"],
      "Resource": ["arn:aws:s3:::secret*"]
    }
  ]
}
```

:::info
MinIO command line interface, `mc`, can be used to do all of the above:

```sh
mc alias set minio-confiance https://minio-storage.apps.confianceai-public.irtsysx.fr <access-key> <secret-key>
mc admin policy add minio-confiance <policy-name> <policy-json-file>
```

:::

All the defined policies can be found [on a Gitlab repository](https://git.irt-systemx.fr/confianceai/ec_1/fa2_infrastructure/minio-policies).
